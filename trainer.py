import torch
import torch.nn as nn
import torch.optim as optim

from model import Net
from dataset import generate_labels, generate_partition, Dataset


def main():
    use_cuda = torch.cuda.is_available()
    device = torch.device('cuda:0' if use_cuda else 'cpu')
    torch.backends.cudnn.benchmark = True

    partition = generate_partition() # e.g. {'train': ['id-1', 'id-2', 'id-3'], 'validation': ['id-4']}
    labels = generate_labels() # load from episode label dict

    # Generators
    training_set = Dataset(partition['train'], labels)
    training_generator = torch.utils.data.DataLoader(training_set, batch_size=32, shuffle=True, num_workers=6)

    validation_set = Dataset(partition['validation'], labels)
    validation_generator = torch.utils.data.DataLoader(validation_set, batch_size=32, shuffle=True, num_workers=6)

    # Init neural net
    net = Net()

    # Define loss function and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    max_epochs = 2

    for epoch in range(max_epochs):
        training_loss = 0.0
        for i, (local_batch, local_labels) in enumerate(training_generator):
            optimizer.zero_grad()

            outputs = net(local_batch)
            loss = criterion(outputs, local_labels)
            loss.backward()
            optimizer.step()

            # print stats
            training_loss += loss.item()
            # if i % 10 == 9:
            print('[%d, %5d] loss: %.3f' % (epoch + 1, i + 1, loss.item() / (i + 1)))

        validation_loss = 0.0
        with torch.set_grad_enabled(False):
            for local_batch, local_labels in validation_generator:
                # local_batch, local_labels = local_batch.to(device), local_labels.to(device)

                outputs = net(local_batch)
                loss = criterion(outputs, local_labels)
                validation_loss += loss.item()

        print(f'Epoch {epoch + 1}: train loss = {training_loss / len(training_generator):.3f}, '
              f'val loss = {validation_loss / len(validation_generator):.3f}')

    print('Finished Training')


if __name__ == '__main__':
    main()
